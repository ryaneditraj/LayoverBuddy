import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app as app_module
from airport_info import get_best_airport
from layovers import calculate_final_score
from layovers import get_layovers
from layovers import get_scores
from layovers import get_top_layovers
from layovers import route_exists
from layovers import score_breakdown
from recommendations import get_recommendation
from storage import load_json


class LayoverBuddyTests(unittest.TestCase):
    def setUp(self):
        self.flask = app_module.app
        self.flask.config["TESTING"] = True
        self.client = self.flask.test_client()

    def test_import_does_not_start_the_server(self):
        completed = subprocess.run(
            [sys.executable, "-c", "import app"],
            cwd=ROOT,
            timeout=8,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_json_reads_do_not_depend_on_the_working_directory(self):
        previous = os.getcwd()
        try:
            os.chdir("/")
            self.assertEqual(len(load_json("airport_info.json")), 6)
        finally:
            os.chdir(previous)

    def test_load_json_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            load_json("../routes.json")

    def test_published_route_scores_stay_stable(self):
        scores = get_scores()
        airports = load_json("airport_info.json")
        expected = {
            "Singapore": 223,
            "Istanbul": 207,
            "Dubai": 200,
            "Doha": 194,
        }
        for city, total in expected.items():
            self.assertEqual(calculate_final_score(city, scores, airports), total)
            self.assertEqual(score_breakdown(city, scores, airports)["total"], total)

    def test_score_bonus_boundaries(self):
        def total(city_time, best_hours):
            return calculate_final_score(
                "Test",
                {"Test": 10},
                {
                    "Test": {
                        "airport_score": 10,
                        "city_time": city_time,
                        "best_hours": best_hours,
                    }
                },
            )

        self.assertEqual(total(30, 8), 50)
        self.assertEqual(total(31, 7), 38)
        self.assertEqual(total(45, 6), 38)
        self.assertEqual(total(46, 5), 27)
        self.assertEqual(get_recommendation(27), "Not recommended.")
        self.assertEqual(get_recommendation(223), "Excellent layover. Highly recommended.")

    def test_top_layovers_use_the_base_score(self):
        top = get_top_layovers("New York", 2)
        self.assertEqual([item["name"] for item in top], ["Singapore", "Istanbul"])

    def test_destination_lookup_ignores_case_and_space(self):
        self.assertEqual(get_layovers("new york"), get_layovers("New York"))
        self.assertTrue(route_exists("  New   York "))
        self.assertEqual(get_layovers("Mars"), [])

    def test_home_search_and_ranking_order(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Choose the city you wait in.", home.data)

        response = self.client.get(
            "/search",
            query_string={"from_city": "Chennai", "to_city": "New York"},
        )
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertLess(text.index("Singapore"), text.index("Istanbul"))
        self.assertLess(text.index("Istanbul"), text.index("Dubai"))
        self.assertLess(text.index("Dubai"), text.index("Doha"))
        self.assertIn("223", text)
        self.assertIn("Marina Bay Sands", text)
        self.assertIn("Excellent layover. Highly recommended.", text)

    def test_reflected_markup_is_escaped(self):
        airport = self.client.get(
            "/airport",
            query_string={"name": "<script>alert(1)</script>"},
        )
        self.assertEqual(airport.status_code, 404)
        self.assertNotIn(b"<script>alert", airport.data)
        self.assertIn(b"&lt;script&gt;", airport.data)

        search = self.client.get(
            "/search",
            query_string={
                "from_city": "<img src=x onerror=alert(1)>",
                "to_city": "<img src=x onerror=alert(1)>",
            },
        )
        self.assertNotIn(b"<img src=x", search.data)
        self.assertIn(b"&lt;img src=x onerror=alert(1)&gt;", search.data)

        huge = "A" * 500
        limited = self.client.get(
            "/search",
            query_string={"from_city": huge, "to_city": "New York"},
        )
        text = limited.get_data(as_text=True)
        self.assertIn("A" * 80, text)
        self.assertNotIn("A" * 81, text)

    def test_known_airport_stats_and_about(self):
        airport = self.client.get("/airport", query_string={"name": "singapore"})
        self.assertEqual(airport.status_code, 200)
        self.assertIn(b"Gardens by the Bay", airport.data)
        self.assertIn(b"One of the best airports in the world.", airport.data)

        stats = self.client.get("/stats")
        self.assertEqual(stats.status_code, 200)
        self.assertIn(get_best_airport().encode(), stats.data)
        self.assertIn(b"98", stats.data)

        about = self.client.get("/about")
        self.assertEqual(about.status_code, 200)
        self.assertIn(b"How does LayoverBuddy score a layover airport?", about.data)

    def test_security_headers_and_discovery_files(self):
        home = self.client.get("/")
        self.assertEqual(home.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(home.headers["X-Frame-Options"], "DENY")
        self.assertNotIn("unsafe-inline", home.headers["Content-Security-Policy"])
        self.assertIn('rel="canonical"', home.get_data(as_text=True))
        self.assertIn("og:title", home.get_data(as_text=True))

        markup = home.get_data(as_text=True)
        match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            markup,
        )
        self.assertIsNotNone(match)
        linked = json.loads(match.group(1))
        self.assertEqual(linked["@type"], "WebApplication")
        self.assertEqual(linked["name"], "LayoverBuddy")

        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertIn(b"Sitemap:", robots.data)
        self.assertNotIn(b"__SITE_URL__", robots.data)

        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn(b"Singapore", sitemap.data)
        self.assertNotIn(b"__SITE_URL__", sitemap.data)

        llms = self.client.get("/llms.txt")
        self.assertEqual(llms.status_code, 200)
        self.assertIn(b"LayoverBuddy", llms.data)

        about = self.client.get("/about")
        about_ld = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            about.get_data(as_text=True),
        )
        about_data = json.loads(about_ld.group(1))
        types = [node["@type"] for node in about_data["@graph"]]
        self.assertIn("FAQPage", types)

    def test_search_pages_are_not_indexed(self):
        response = self.client.get(
            "/search",
            query_string={"from_city": "Chennai", "to_city": "new york"},
        )
        self.assertIn(b'content="noindex, follow"', response.data)

    def test_missing_page(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"That page is not on the board.", response.data)


if __name__ == "__main__":
    unittest.main()

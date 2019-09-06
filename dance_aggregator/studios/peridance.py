import logging
from datetime import date, timedelta
from dateutil import parser
from typing import List

import bs4
import requests

from dance_aggregator.lib import DanceStudioScraper
from dance_aggregator.models import Event

logger = logging.getLogger("dance_aggregator")


class Peridance(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name="Peridance Center")
        self.calendar_id = "nv2j59b7lpa07ckovkhgr9g4bc@group.calendar.google.com"

    def parse_day_schedule(self, date: date) -> List[Event]:
        base_url = "http://www.peridance.com/openclasses.cfm"
        day_soup = bs4.BeautifulSoup(
            requests.post(base_url, data={"testdate": date}).content,
            features="html.parser",
        )

        row_children = day_soup.find_all("font", {"face": "Helvetica, Arial"})
        rows = [child.parent.parent.parent for child in row_children]

        event_records = []
        for row in rows:
            # Get class category from sibling row
            category_row = row

            # -1 because one of the strings is a NavigableString not a Tag
            try:
                while (
                    category_row.find("center") is None
                    or category_row.find("center") == -1
                ):
                    category_row = category_row.previous_sibling
            except AttributeError as e:
                logger.error(f"Error parsing class {row.text.strip()} - {e}")
                continue
            category = category_row.text

            level = row.div.text.strip()

            instructor = row.font.text

            title = f"{level} {category} - {instructor}"

            if "$(function" in title:
                continue

            day_str = date.strftime("%Y-%m-%d")
            start_time_str, end_time_str = row.find(
                "td", {"align": "center"}
            ).text.split(' -')
            start_datetime, end_datetime = (
                parser.parse(f"{day_str} {start_time_str}"),
                parser.parse(f"{day_str} {end_time_str}"),
            )

            event_record = Event(
                title=title,
                instructor=instructor,
                studio=self.studio_name,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                url=base_url,
                location="126 East 13th Street New York, NY 10003",
            )
            event_records.append(event_record)
        return event_records

    # def parse_day_schedule(self, date: date) -> List[Event]:
    #     base_url = "http://www.peridance.com/openclasses.cfm"
    #     day_soup = bs4.BeautifulSoup(
    #         requests.post(base_url, data={"testdate": date}).content, features="html.parser"
    #     )

    #     raw = pd.read_html(str(day_soup.table))[1]
    #     no_field_name_rows = raw[raw.iloc[:, 0] != "Time"]
    #     non_cat_rows_mask = no_field_name_rows.iloc[:, 0].map(lambda x: ":" in x)
    #     no_field_name_rows["category"] = no_field_name_rows[0]
    #     no_field_name_rows.loc[non_cat_rows_mask, "category"] = np.nan
    #     no_field_name_rows["category"] = no_field_name_rows["category"].fillna(
    #         method="ffill"
    #     )
    #     schedule = no_field_name_rows[
    #         no_field_name_rows.apply(lambda x: x.nunique() > 1, axis=1)
    #     ]
    #     schedule.columns = ["time", "level", "instructor", "category"]

    #     schedule["title"] = schedule[["level", "category"]].apply(
    #         lambda x: f"{x[1]} - {x[0]}", axis=1
    #     )
    #     day_str = date.strftime("%Y-%m-%d")
    #     schedule["start_datetime"] = schedule.time.map(
    #         lambda x: pd.to_datetime(f"{day_str} {x.split(' -')[0]}")
    #     ).dt.to_pydatetime()
    #     schedule["end_datetime"] = schedule.time.map(
    #         lambda x: pd.to_datetime(f"{day_str} {x.split(' -')[1]}")
    #     ).dt.to_pydatetime()

    #     event_dicts = schedule.to_dict(orient="records")
    #     event_records = [
    #         Event(
    #             title=event_dict["title"],
    #             instructor=event_dict["instructor"],
    #             studio=self.studio_name,
    #             start_datetime=event_dict["start_datetime"],
    #             end_datetime=event_dict["end_datetime"],
    #             url=base_url,
    #             location="126 East 13th Street New York, NY 10003",
    #         )
    #         for event_dict in event_dicts
    #     ]
    #     return event_records

    def get_events(self) -> List[Event]:
        current_date = date.today()
        events: List[Event] = []
        for _ in range(31):
            events += self.parse_day_schedule(current_date)
            current_date += timedelta(days=1)
        return events

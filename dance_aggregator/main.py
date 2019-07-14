import logging

from dance_aggregator.studios import gibney


INCLUDED_STUDIOS = [gibney.Gibney]


def main():
    output = []
    for Studio in INCLUDED_STUDIOS:
        studio = Studio()
        logging.info(f"Collecting events for {studio.studio_name}")
        studio.get_events()
        output += studio.as_records()

        # Doesn't do anything with records yet


if __name__ == "__main__":
    main()

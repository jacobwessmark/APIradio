import requests
from datetime import datetime, timedelta
import pytz
import re


def get_stations():
    """
    Hämta en lista över radiostationer från Sveriges Radio API.
    Returnerar en lista av dictionaries som representerar varje station.
    """
    url = "https://api.sr.se/api/v2/channels?format=json"
    response = requests.get(url)
    stations = response.json()['channels']
    return stations


def print_stations(stations):
    """
    Skriv ut en lista över radiostationer.
    Tar en lista av stationer och skriver ut varje stations namn.
    """
    for idx, station in enumerate(stations, start=1):
        print(f"{idx}. {station['name']}")


def convert_utc_to_local(utc_time_str):
    """
    Konvertera UTC-tidsträng till lokal tid.
    Returnerar ett datetime-objekt.
    """
    numbers = re.findall(r'\d+', utc_time_str)
    milliseconds = int("".join(numbers))
    seconds = milliseconds / 1000
    epoch = datetime(1970, 1, 1)
    utc_time = epoch + timedelta(seconds=seconds)
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    local_time = utc_time.astimezone(pytz.timezone('Europe/Stockholm'))
    return local_time


def get_schedule(channel_id):
    """
    Hämta och skriv ut tablån för en specifik kanal.
    Tar en kanals ID och skriver ut de nästa 5 programmen från nuvarande tid.
    """
    now = datetime.now(pytz.timezone('Europe/Stockholm'))
    url = f"https://api.sr.se/api/v2/scheduledepisodes?channelid={channel_id}&size=100&format=json"
    response = requests.get(url).json()
    counter = 0  # för antalet nästa utskrivna program
    stars = "*" * 10

    for program in response['schedule']:
        program_start = convert_utc_to_local(program['starttimeutc'])
        program_end = convert_utc_to_local(program['endtimeutc'])

        # Kollar om programmet sänds just nu
        if program_start <= now < program_end:
            print(f"Just nu sänds:\n{stars} {program['title']} {stars}")
            print(program['description'])
            print(f"\n{program['channel']['name']} tablå: ")

        # Skriver ut kommande program
        elif program_start > now:
            print(program_start.strftime('%H:%M'), " - ", program['title'])
            counter += 1

        # Avbryter efter 5 kommande program
        if counter == 5:
            break


def main():
    """
    Huvudfunktionen för programmet.
    Hanterar användarinteraktion och anropar andra funktioner.
    """
    try:
        stations = get_stations()
        print_stations(stations)
        choice = int(input("Välj en radiostation: "))
        print()
        chosen_station = stations[choice - 1]
        get_schedule(chosen_station['id'])

    except requests.RequestException:
        print("Ett fel uppstod vid anslutning till Sveriges Radios API.")
    except (IndexError, ValueError):
        print("Ogiltigt val. Vänligen välj en korrekt radiostation.")


if __name__ == "__main__":
    main()

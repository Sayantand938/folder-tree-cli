# scripts/generate_mock_data.py
import typer
import pendulum
import random
import xxhash
from focus_forge.db.database import add_session, update_session_end_time, DB_PATH, initialize_database
import sqlite3
from rich.console import Console

console = Console()

def generate_mock_data(
    start_date_str: str = typer.Option(..., prompt="Enter start date (YYYY-MM-DD)"),
    end_date_str: str = typer.Option(..., prompt="Enter end date (YYYY-MM-DD)"),
):
    """Generates mock session data between the specified dates."""

    try:
        start_date = pendulum.parse(start_date_str).to_date_string()
        end_date = pendulum.parse(end_date_str).to_date_string()

        start_date = pendulum.parse(start_date).start_of('day')
        end_date = pendulum.parse(end_date).end_of('day')


    except (ValueError, pendulum.exceptions.ParserError):
        console.print("[bold red]Invalid date format. Use YYYY-MM-DD.[/bold red]")
        raise typer.Exit(1)

    if start_date > end_date:
        console.print("[bold red]Start date must be before end date.[/bold red]")
        raise typer.Exit(1)

    initialize_database()  # Ensure the database is initialized

    current_date = start_date
    while current_date <= end_date:
        current_time = current_date.replace(hour=8, minute=0, second=0)  # Start at 8 AM
        end_of_day = current_date.replace(hour=23, minute=30, second=0) #upto 11:30 PM

        while current_time < end_of_day:
            # Generate session duration (25-35 minutes)
            duration_minutes = random.randint(25, 35)
            duration_seconds = duration_minutes * 60
            end_time = current_time.add(seconds=duration_seconds)

            # Check for overlap with end_of_day
            if end_time > end_of_day:
                end_time = end_of_day
                duration_seconds = (end_time - current_time).in_seconds()

            # Generate session ID and add to the database
            session_id = xxhash.xxh64(current_time.to_datetime_string()).hexdigest()
            try:
                add_session(session_id, current_time.to_iso8601_string())
                update_session_end_time(session_id, end_time.to_iso8601_string(), duration_seconds)
                console.print(f"[green]Added session: {current_time.to_time_string()} - {end_time.to_time_string()} ({duration_minutes} mins) on {current_date.to_date_string()}[/green]")
            except sqlite3.Error as e:
                console.print(f"[bold red]Database error: {e}[/bold red]")
                raise typer.Exit(1)


            # Generate gap (35-45 minutes)
            gap_minutes = random.randint(35, 45)
            current_time = end_time.add(minutes=gap_minutes)

            if current_time >= end_of_day:
                break # No more sessions today

        current_date = current_date.add(days=1)  # Move to the next day

    console.print("[bold green]Mock data generation complete![/bold green]")


if __name__ == "__main__":
    typer.run(generate_mock_data)
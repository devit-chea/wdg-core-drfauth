import os
import re
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deletes the specified Django app and all related files."

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="The name of the app to delete.")

    def handle(self, *args, **options):
        app_name = options["name"]
        target = os.path.join(os.getcwd(), "apps", app_name)

        # Check if the app directory exists
        if not os.path.exists(target):
            self.stdout.write(
                self.style.ERROR(f"The app '{app_name}' does not exist at '{target}'.")
            )
            return

        # Confirm app deletion
        self.stdout.write(
            self.style.WARNING(
                f"Are you sure you want to delete the app '{app_name}' at '{target}'? [y/n]"
            )
        )
        confirmation = input().strip().lower()

        if confirmation != "y":
            self.stdout.write(self.style.ERROR("App deletion canceled."))
            return

        # Delete app directory and its contents
        self._remove_app_directory(target)

        # Remove app from LOCAL_APPS in settings
        self._remove_app_from_local_apps(app_name)

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' deleted successfully!"))

    def _remove_app_directory(self, target):
        """Delete the app directory and its contents."""
        try:
            for root, dirs, files in os.walk(target, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(target)  # Remove the main app directory itself
            self.stdout.write(self.style.SUCCESS(f"Deleted directory: {target}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error while deleting the app directory: {e}")
            )

    def _remove_app_from_local_apps(self, app_name):
        """Remove the app from the LOCAL_APPS list in the settings.py."""
        settings_path = os.path.join(settings.BASE_DIR, "config", "settings", "base.py")

        # Generate the app configuration class name
        app_class_name = app_name.capitalize()
        if "_" in app_name:
            new_appname = "".join([part.capitalize() for part in app_name.split("_")])
            app_class_name = f"{new_appname}Config"
        else:
            app_class_name = f"{app_class_name}Config"

        app_config = (
            f"    'apps.{app_name}.apps.{app_class_name}',"  # Ensure the format matches
        )

        try:
            with open(settings_path, "r+") as file:
                content = file.read()

                # Regular expression to find the app configuration with optional space and comma handling
                pattern = re.compile(
                    r"^\s*['\"]apps\."
                    + re.escape(app_name)
                    + r"\.apps\."
                    + re.escape(app_class_name)
                    + r"['\"],?\s*\n?",
                    re.MULTILINE,
                )

                # Remove the matched app configuration
                content, num_replacements = re.subn(pattern, "", content)

                if num_replacements > 0:
                    # Clean up the formatting:
                    content = re.sub(
                        r"\s*,\s*\n\s*\]", "\n]", content
                    )  # Remove trailing commas before closing bracket
                    content = re.sub(
                        r"\n\s*,\n", "\n", content
                    )  # Ensure no commas before closing bracket
                    content = re.sub(
                        r"\n\s*\]$", "\n]", content
                    )  # Fix if the closing bracket is alone

                    # Count number of apps left
                    apps_left = len(
                        re.findall(r"^\s*'", content, re.MULTILINE)
                    )  # Count number of apps

                    if apps_left == 1:
                        # Ensure there’s a comma before the closing bracket if only one app remains
                        content = content.rstrip() + ",\n]"

                    # Write the updated content to the file
                    file.seek(0)
                    file.write(content)
                    file.truncate()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Removed '{app_name}' from LOCAL_APPS in settings.py"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"App '{app_name}' not found in LOCAL_APPS in settings.py"
                        )
                    )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f"settings.py not found. Please remove the app manually from your settings."
                )
            )

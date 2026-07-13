

def extract_zip(zip_path, dest_folder):
    import os
    import zipfile
    dest_folder = os.path.abspath(dest_folder)

    with zipfile.ZipFile(zip_path, "r") as z:
        # Check safety of zipfile
        for member in z.namelist():
            member_path = os.path.abspath(os.path.join(dest_folder, member))
            if not member_path.startswith(dest_folder + os.sep) and member_path != dest_folder:
                raise ValueError(f"Unsafe path in zip: {member}")

        z.extractall(dest_folder)

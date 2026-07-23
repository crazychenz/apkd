import subprocess

def create_avd(avd, image):
    
    cmd = ["avdmanager", "create", "avd", "--name", avd, "--package", image,
    ]
    # if args.device:
    #     cmd += ["--device", device]
    # if args.force:
    #     cmd.append("--force")  # overwrite existing AVD with same name, no prompt for that either

    subprocess.run(cmd,
        input="no\n",   # answer to "Do you wish to create a custom hardware profile?"
        text=True,
        check=True,
    )


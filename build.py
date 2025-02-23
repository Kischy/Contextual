#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path

project_dir = Path(__file__).parent.absolute()
meson_sub_dir = "meson-src"

def run_command(cmd, cwd=None):
    """Run a command and handle errors"""
    try:
        print(f"Run command: {' '.join(cmd)} in {cwd}")
        subprocess.run(cmd, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Error: {e}")
        sys.exit(1)

def setup_build_directory(build_type):
    """Create and setup build directory"""
    build_dir = Path(f"build/{build_type}")
    build_dir.mkdir(exist_ok=True, parents=True)
    return build_dir

def install_dependencies(build_dir, build_type):
    """Install dependencies using Conan"""
    print(f"Installing dependencies with Conan ({build_type} build)...")
    cmd = [
        "conan", "install", ".",
        "--output-folder", str(build_dir),
        "--build=missing",
        "-s", f"build_type={build_type.capitalize()}"
    ]
    run_command(cmd)

def configure_meson(build_dir, build_type):
    """Configure project with Meson"""
    print("Configuring with Meson...")
    cmd = [
        "meson", "setup",
        "--reconfigure",
        "--buildtype", build_type.lower(),
        "--native-file", "conan_meson_native.ini" ,
        str(project_dir),meson_sub_dir
    ]
    run_command(cmd, cwd=build_dir)

def build_project(build_dir):
    """Build the project"""
    print("Building the project...")
    run_command(["meson", "compile", "-C", meson_sub_dir], cwd=build_dir)

def test_project(build_dir):
    """TEst the project"""
    print("Testing the project...")
    run_command(["meson", "test", "-C", meson_sub_dir], cwd=build_dir)

def main():
    parser = argparse.ArgumentParser(description="Build script for Conan/Meson project")
    parser.add_argument(
        "--build-type",
        choices=["Debug", "Release"],
        default="Debug",
        help="Build type (Debug or Release)"
    )
    args = parser.parse_args()

    # Setup build directory
    build_dir = setup_build_directory(args.build_type)

    # Install dependencies
    install_dependencies(build_dir, args.build_type)

    # Configure and build
    configure_meson(build_dir, args.build_type)
    build_project(build_dir)

    # Test project
    test_project(build_dir)


    print("Build completed successfully!")

if __name__ == "__main__":
    main()
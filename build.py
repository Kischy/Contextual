#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
import argparse
from pathlib import Path
from enum import Enum

class BuildType(Enum):
    DEBUG = "Debug"
    RELEASE = "Release"

    def __str__(self):
        return self.value

def run_command(command, cwd=None):
    """Run a shell command and handle errors"""
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        return False

def clean_build_directory(script_dir, build_type):
    """Clean the build directory for specific build type"""
    build_dir = script_dir / "build" / str(build_type)
    if build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
    
    # Clean Conan-generated files in the root
    for file in script_dir.glob("*.ini"):
        file.unlink()
    for file in script_dir.glob("*.pc"):
        file.unlink()

def get_conan_profile(build_type):
    """Generate Conan profile settings based on build type"""
    if build_type == BuildType.DEBUG:
        return [
            "-s", "build_type=Debug",
            "-s:h", "build_type=Debug"
        ]
    else:
        return [
            "-s", "build_type=Release",
            "-s:h", "build_type=Release"
        ]

def build_project(build_type=BuildType.RELEASE, rebuild=False):
    """Build the project using Conan and Meson"""
    
    # Get the script's directory
    script_dir = Path(__file__).parent.absolute()
    
    # If rebuilding, clean first
    if rebuild:
        clean_build_directory(script_dir, build_type)

    # Create build directory if it doesn't exist
    build_dir = script_dir / "build" / str(build_type)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Get Conan settings for the build type
    conan_settings = get_conan_profile(build_type)
    
    # Run Conan install with appropriate settings
    print(f"\nRunning Conan install for {build_type}...")
    conan_cmd = ["conan", "install", ".", "--output-folder=.", "--build=missing"]
    conan_cmd.extend(conan_settings)
    if not run_command(" ".join(conan_cmd), script_dir):
        return False

    # Run Meson setup
    print(f"\nRunning Meson setup for {build_type}...")
    generators_path = build_dir / "generators" / "conan_meson_native.ini"
    
    meson_options = []
    if build_type == BuildType.DEBUG:
        meson_options.extend([
            "--buildtype=debug",
            "-Ddebug=true",
            "-Doptimization=0"
        ])
    else:
        meson_options.extend([
            "--buildtype=release",
            "-Ddebug=false",
            "-Doptimization=3"
        ])

    meson_command = [
        "meson", "setup",
        "--reconfigure",
        "--cross-file", str(generators_path),
        *meson_options,
        str(build_dir)
    ]
    
    if not run_command(" ".join(meson_command), script_dir):
        return False

    # Run Ninja build
    print(f"\nRunning Ninja build for {build_type}...")
    if not run_command("ninja", build_dir):
        return False

    # Run tests
    print(f"\nRunning tests for {build_type}...")
    if not run_command("ninja test", build_dir):
        return False

    print(f"\n{build_type} build completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Build script for the project')
    parser.add_argument('--rebuild', action='store_true', 
                      help='Clean and rebuild everything')
    parser.add_argument('--type', type=BuildType, choices=list(BuildType), 
                      default=BuildType.RELEASE,
                      help='Build type (Debug or Release)')
    args = parser.parse_args()

    return 0 if build_project(build_type=args.type, rebuild=args.rebuild) else 1

if __name__ == "__main__":
    sys.exit(main())
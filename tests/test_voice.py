#!/usr/bin/env python3
"""
Test script for the voice synthesizer system
============================================

This script tests the voice synthesis system with different backends
and provides a simple command-line interface for testing.
"""

import logging
from timecraft_ai.ai.voice_synthesizer import VoiceSynthesizer, create_voice_synthesizer, test_voice_synthesis
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def main():
    """Main test function"""
    print("🎤 TimeCraft AI - Voice Synthesizer Test")
    print("=" * 50)

    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)

    try:
        # Test 1: Create synthesizer and check status
        print("\n📋 Test 1: Creating voice synthesizer...")
        synthesizer = create_voice_synthesizer(lang="en", debug=True)

        status = synthesizer.get_status()
        print(f"Status: {status}")

        # Test 2: Test basic synthesis
        print("\n🗣️ Test 2: Testing voice synthesis...")
        test_text = "Hello! This is a test of the TimeCraft AI voice synthesis system."

        try:
            synthesizer.synthesize_and_play(test_text)
            print("✅ Voice synthesis test completed!")
        except Exception as e:
            print(f"⚠️ Voice synthesis test failed: {e}")

        # Test 3: Test different languages (if available)
        print("\n🌍 Test 3: Testing available languages...")
        languages = synthesizer.get_available_languages()
        print(f"Available languages: {languages}")

        # Test 4: Test different voices (if available)
        print("\n🎭 Test 4: Testing available voices...")
        voices = synthesizer.get_available_voices()
        # Show first 5
        print(f"Available voices: {list(voices.keys())[:5]}...")

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

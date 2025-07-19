"""
TimeCraft AI Command Line Interface
==================================

CLI profissional para análise de dados e assistente de voz hands-free.
"""

import click
import sys
import os
from pathlib import Path
import time
import json


@click.group()
@click.version_option(version="1.1.3")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def timecraft_ai(ctx, verbose):
    """
    🚀 TimeCraft AI - Intelligent Data Analysis & Voice Assistant

    A powerful CLI for hands-free data analysis, AI predictions, and voice control.

    Examples:
        timecraft-ai analyze data.csv --periods 60
        timecraft-ai voice --passive
        timecraft-ai speak "Hello, world!"
        timecraft-ai status
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

    if verbose:
        click.echo("🔧 Verbose mode enabled")


@timecraft_ai.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for results')
@click.option('--periods', '-p', default=30, help='Number of prediction periods')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'html']), default='json', help='Output format')
@click.option('--model', '-m', type=click.Choice(['linear', 'arima', 'prophet']), default='linear', help='Prediction model')
@click.pass_context
def analyze(ctx, file, output, periods, format, model):
    """📊 Analyze data file with AI predictions

    Supports CSV, JSON, and Excel files for time series analysis and forecasting.
    """
    try:
        click.echo(f"🔍 Analyzing {file} with {model} model...")

        if ctx.obj.get('verbose'):
            click.echo(f"   📈 Periods: {periods}")
            click.echo(f"   📄 Format: {format}")

        # Import here to avoid loading heavy modules unless needed
        from timecraft_ai import TimeCraftModel

        # Initialize TimeCraft
        with click.progressbar(length=3, label='Processing') as bar:
            bar.update(1)

            tc = TimeCraftModel(data=file)

            bar.update(1)

            tc.fit_model()

            bar.update(1)

        # Make predictions
        click.echo("🔮 Generating predictions...")
        forecast = tc.make_predictions(periods=periods)

        # Save or display results
        if output:
            output_path = Path(output)
            if format == 'csv':
                forecast.to_csv(output_path, index=False)
            elif format == 'html':
                forecast.to_html(output_path, index=False, escape=False)
            else:  # json
                forecast.to_json(output_path, orient='records',
                                 date_format='iso', indent=2)

            click.echo(f"✅ Results saved to {output_path}")
            click.echo(f"📊 Generated {len(forecast)} predictions")
        else:
            click.echo("📈 Forecast preview (first 10 rows):")
            click.echo("-" * 50)
            if hasattr(forecast, 'head'):
                click.echo(forecast.head(10).to_string())
            else:
                click.echo(str(forecast)[
                           :500] + "..." if len(str(forecast)) > 500 else str(forecast))

    except ImportError as e:
        click.echo(f"❌ Missing dependencies for analysis: {e}", err=True)
        click.echo("💡 Try: pip install pandas scikit-learn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Analysis error: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@timecraft_ai.command()
@click.option('--passive', '-p', is_flag=True, help='Enable passive listening mode')
@click.option('--lang', '-l', default='pt-br', help='Voice language (pt-br, en)')
@click.option('--sensitivity', '-s', default=0.5, type=float, help='Hotword detection sensitivity (0.0-1.0)')
@click.pass_context
def voice(ctx, passive, lang, sensitivity):
    """🎤 Start voice assistant mode

    Interactive voice assistant with hands-free commands and responses.
    """
    try:
        click.echo("🎤 Initializing TimeCraft Voice Assistant...")
        click.echo("=" * 60)

        if passive:
            click.echo("🎧 Passive listening mode enabled")
            click.echo(f"   Wake words: 'Hey TimeCraft', 'Oi TimeCraft'")
            click.echo(f"   Language: {lang}")
            click.echo(f"   Sensitivity: {sensitivity}")

        click.echo("💡 Say 'Hey TimeCraft' to activate or Ctrl+C to exit")
        click.echo("=" * 60)

        # Import voice system
        from timecraft_ai import AudioProcessor

        # Initialize and start system
        system = AudioProcessor()

        if system._initialize_audio_stream():
            try:
                while True:
                    time.sleep(1)

                    # Show stats periodically if verbose
                    if ctx.obj.get('verbose') and int(time.time()) % 30 == 0:
                        stats = system.metrics
                        click.echo(f"⚡ Stats: {stats['hotwords_detected']} activations, "
                                   f"{stats['commands_processed']} commands")

            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping voice assistant...")
            finally:
                system.cleanup()
                system._print_metrics()
        else:
            click.echo("❌ Failed to start voice system", err=True)
            sys.exit(1)

        click.echo("👋 Voice assistant stopped.")

    except ImportError as e:
        click.echo(f"❌ Voice features not available: {e}", err=True)
        click.echo(
            "💡 Install voice dependencies or check audio hardware", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Voice system error: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@timecraft_ai.command()
@click.argument('text')
@click.option('--lang', '-l', default='pt-br', help='Voice language')
@click.option('--speed', '-s', default=1.0, type=float, help='Speech speed (0.5-2.0)')
@click.pass_context
def speak(ctx, text, lang, speed):
    """🔊 Speak text using voice synthesis

    Convert text to speech using the TimeCraft voice engine.
    """
    try:
        click.echo(f"🔊 Speaking: '{text}'")

        # Import voice synthesizer
        from timecraft_ai.ai import VoiceSynthesizer

        synthesizer = VoiceSynthesizer()
        synthesizer.speak(text)

        if ctx.obj.get('verbose'):
            click.echo(f"   Language: {lang}")
            click.echo(f"   Speed: {speed}")

        click.echo("✅ Speech completed")

    except ImportError as e:
        click.echo(f"❌ Voice synthesis not available: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Speech error: {e}", err=True)
        sys.exit(1)


@timecraft_ai.command()
@click.pass_context
def status(ctx):
    """📋 Show system status and available features

    Comprehensive health check of all TimeCraft AI components.
    """
    click.echo("🚀 TimeCraft AI System Status")
    click.echo("=" * 50)

    try:
        # Check core modules
        # try:
        # from timecraft_ai import AI_MODULES_AVAILABLE, MCP_SERVER_AVAILABLE
        # click.echo(
        #     f"🧠 AI Modules: {'✅ Available' if AI_MODULES_AVAILABLE else '❌ Not Available'}")
        # click.echo(
        #     f"🌐 MCP Server: {'✅ Available' if MCP_SERVER_AVAILABLE else '❌ Not Available'}")
        # except ImportError:
        #     click.echo("🧠 AI Modules: ❌ Import Error")
        #     click.echo("🌐 MCP Server: ❌ Import Error")

        # Check voice capabilities
        try:
            from timecraft_ai.ai import AudioProcessor, VoiceSynthesizer, HotwordDetector
            click.echo("🎤 Voice Recognition: ✅ Available")
            click.echo("🔊 Voice Synthesis: ✅ Available")
            click.echo("🎯 Hotword Detection: ✅ Available")
        except ImportError as e:
            click.echo("🎤 Voice Features: ❌ Not Available")
            if ctx.obj.get('verbose'):
                click.echo(f"   Error: {e}")

        # Check voice model
        model_path = os.environ.get('TIMECRAFT_MODEL_PATH')
        if not model_path:
            # Try default path
            from timecraft_ai.ai.audio_processor import get_model_path
            try:
                model_path = get_model_path()
            except:
                model_path = None

        if model_path and Path(model_path).exists():
            model_size = Path(model_path).stat().st_size / (1024*1024)  # MB
            click.echo(f"🗣️ Voice Model: ✅ Found ({model_size:.1f} MB)")
            if ctx.obj.get('verbose'):
                click.echo(f"   Path: {model_path}")
        else:
            click.echo("🗣️ Voice Model: ❌ Not found")
            if ctx.obj.get('verbose'):
                click.echo(f"   Expected: {model_path or 'Unknown'}")

        # Check data analysis capabilities
        try:
            from timecraft_ai.core import TimeCraftAI, DatabaseConnector
            click.echo("📊 Data Analysis: ✅ Available")
            click.echo("🗄️ Database Support: ✅ Available")
        except ImportError:
            click.echo("📊 Data Analysis: ❌ Not Available")
            click.echo("🗄️ Database Support: ❌ Not Available")

        # System info
        click.echo("\n💻 System Information:")
        click.echo(f"   Python: {sys.version.split()[0]}")
        click.echo(f"   Platform: {sys.platform}")
        click.echo(f"   Working Dir: {os.getcwd()}")

        # Environment variables
        if ctx.obj.get('verbose'):
            click.echo("\n🔧 Environment Variables:")
            env_vars = ['TIMECRAFT_MODEL_PATH', 'PICOVOICE_ACCESS_KEY']
            for var in env_vars:
                value = os.environ.get(var, 'Not set')
                click.echo(f"   {var}: {value}")

    except Exception as e:
        click.echo(f"❌ Status check error: {e}")
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)


@timecraft_ai.command()
@click.option('--host', '-h', default='127.0.0.1', help='Server host')
@click.option('--port', '-p', default=8000, type=int, help='Server port')
@click.option('--reload', '-r', is_flag=True, help='Enable auto-reload')
@click.pass_context
def server(ctx, host, port, reload):
    """🌐 Start MCP server

    Launch the Model Context Protocol server for external integrations.
    """
    try:
        click.echo(f"🌐 Starting TimeCraft MCP Server on {host}:{port}")

        if reload:
            click.echo("🔄 Auto-reload enabled")

        if ctx.obj.get('verbose'):
            click.echo(f"   Host: {host}")
            click.echo(f"   Port: {port}")
            click.echo(f"   Reload: {reload}")

        # Import and start server
        from timecraft_ai import mcp_server_app

        click.echo("🚀 Server starting... (Ctrl+C to stop)")
        mcp_server_app.run(initial_value=1)
        click.echo("✅ Server started successfully")

    except ImportError as e:
        click.echo(f"❌ MCP server not available: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Server error: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@timecraft_ai.command()
@click.option('--output', '-o', default='timecraft_config.json', help='Configuration file path')
@click.pass_context
def config(ctx, output):
    """⚙️ Generate configuration file template

    Create a configuration file with all available options.
    """
    try:
        config_template = {
            "voice": {
                "language": "pt-br",
                "model_path": "${TIMECRAFT_MODEL_PATH}",
                "hotword_sensitivity": 0.5,
                "wake_words": [
                    "hey timecraft",
                    "oi timecraft",
                    "olá timecraft",
                    "timecraft ativa"
                ]
            },
            "analysis": {
                "default_periods": 30,
                "default_model": "linear",
                "output_format": "json"
            },
            "server": {
                "host": "127.0.0.1",
                "port": 8000,
                "auto_reload": False
            },
            "logging": {
                "level": "INFO",
                "file": "timecraft.log"
            }
        }

        with open(output, 'w') as f:
            json.dump(config_template, f, indent=2)

        click.echo(f"⚙️ Configuration template created: {output}")
        click.echo("💡 Edit the file to customize your settings")

        if ctx.obj.get('verbose'):
            click.echo("📄 Configuration contents:")
            click.echo(json.dumps(config_template, indent=2))

    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@timecraft_ai.command()
def version():
    """📝 Show detailed version information"""
    click.echo("🚀 TimeCraft AI")
    click.echo("=" * 30)

    try:
        from timecraft_ai import __version__, __author__, __email__, __license__
        click.echo(f"Version: {__version__}")
        click.echo(f"Author: {__author__}")
        click.echo(f"Email: {__email__}")
        click.echo(f"License: {__license__}")
    except ImportError:
        click.echo("Version: Unknown")

    click.echo(f"Python: {sys.version}")
    click.echo(f"Platform: {sys.platform}")


# Hidden command for testing
@timecraft_ai.command(hidden=True)
@click.pass_context
def test(ctx):
    """🧪 Run system tests (hidden command)"""
    click.echo("🧪 Running TimeCraft AI tests...")

    # Basic import test
    try:
        from timecraft_ai import TimeCraftAI
        click.echo("✅ Core imports working")
    except Exception as e:
        click.echo(f"❌ Core import failed: {e}")

    # Voice test
    try:
        from timecraft_ai.ai import AudioProcessor, VoiceSynthesizer
        click.echo("✅ Voice imports working")
    except Exception as e:
        click.echo(f"❌ Voice import failed: {e}")

    click.echo("🎯 Test completed")


# if __name__ == '__main__':
#     timecraft_ai.cli()

# TimeCraft Documentation

This directory contains the documentation for TimeCraft, built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## Building the Documentation

### Prerequisites

Install the required dependencies:

```bash
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin pymdown-extensions
```

Or install with the documentation extra:

```bash
pip install "timecraft[docs]"
```

### Local Development

To serve the documentation locally with live reloading:

```bash
mkdocs serve
```

The documentation will be available at `http://127.0.0.1:8000/`

### Building Static Files

To build the static documentation files:

```bash
mkdocs build
```

The built documentation will be in the `site/` directory.

## Documentation Structure

```
docs/
├── index.md                 # Homepage
├── README.en.md            # English README
├── README.pt-BR.md         # Portuguese README
├── INSTALL.md              # Installation guide
├── INSTALL_AI.md           # AI features installation
├── CODE_OF_CONDUCT.md      # Code of conduct
├── CONTRIBUTING.md         # Contributing guidelines
├── SUPPORT.md              # Support information
├── AUTHORS.md              # Authors and contributors
├── LICENSE                 # License file
├── NOTICE.md               # Notice file
├── SECURITY.md             # Security policy
├── CHANGELOG.md            # Changelog
└── assets/                 # Images and other assets
    └── top_banner.png      # Project banner
```

## Deployment

The documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

### Manual Deployment

To manually deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

## Contributing to Documentation

When contributing to the documentation:

1. Follow the existing structure and style
2. Use proper Markdown formatting
3. Include code examples where appropriate
4. Test the documentation locally before submitting
5. Update the navigation in `mkdocs.yml` if adding new pages

## Configuration

The documentation configuration is in `mkdocs.yml` in the root directory. Key features include:

- **Material Theme**: Modern, responsive design
- **Search**: Built-in search functionality
- **Navigation**: Organized navigation structure
- **Code Highlighting**: Syntax highlighting for code blocks
- **Git Integration**: Automatic revision dates
- **Social Links**: Links to GitHub, LinkedIn, etc.

## Writing Guidelines

- Use clear, concise language
- Include practical examples
- Structure content with proper headings
- Use code blocks for commands and code
- Include screenshots when helpful
- Link to related sections and external resources

For more detailed writing guidelines, see our [Contributing Guide](../CONTRIBUTING.md).

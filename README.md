# ASA Auth Mode

A pre-commit/post-commit hook utility for managing Azure Synapse Analytics authentication modes in JSON configuration
files.

## Overview

This utility automatically converts between `ConnectionString` and `Msi` authentication modes in JSON files within your
repository. It's designed to be used with pre-commit and post-commit hooks to ensure that:

1. Before committing: All JSON files are converted to use `Msi` authentication
2. After committing: Files are converted back to `ConnectionString` for local development

## Usage

### Pre-commit Hook Integration

This tool is designed to be used as a pre-commit and post-commit hook. To integrate it into your project:

1. First, install pre-commit if you haven't already:
   ```bash
   pip install pre-commit
   ```

2. Add the following to your `.pre-commit-config.yaml` file:
   ```yaml
   repos:
     - repo: https://github.com/josefondrej/pre-commit-azure-stream-analytics
       rev: v0.1.0
       hooks:
         - id: asa-auth-mode-pre
           name: ASA Auth Mode (Pre-commit)
           description: Converts ConnectionString to Msi before committing
           language: python
           pass_filenames: false
           always_run: true
         
         - id: asa-auth-mode-post
           name: ASA Auth Mode (Post-commit)
           description: Converts Msi to ConnectionString after committing
           language: python
           stages: [post-commit]
           pass_filenames: false
           always_run: true
   ```

3. Install the pre-commit hooks:
   ```bash
   pre-commit install --hook-type pre-commit --hook-type post-commit
   ```

4. Now, whenever you commit:
    - The pre-commit hook will automatically convert all `AuthenticationMode` from `ConnectionString` to `Msi` before
      committing
    - The post-commit hook will convert them back to `ConnectionString` for your local development environment

## How It Works

The utility:

1. Recursively locates all JSON files in your repository
2. Detects the indentation style of each file to preserve formatting
3. Locates any objects with an `AuthenticationMode` property
4. Updates the value based on the specified direction
5. Preserves the original formatting when writing back to the file

## Features

- Preserves original JSON indentation
- Handles nested JSON structures
- Gracefully skips invalid or non-JSON files
- Reports statistics on processed files
- Maintains encoding when reading/writing files

## Requirements

- Python 3.6+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
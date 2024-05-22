
# AmazonMMC CLI Tool

## Overview

**AmazonMMC** is a command-line interface (CLI) tool designed to facilitate the creation of Amazon Media Entertainment Core (MEC) and Media Manifest Core (MMC) XML files. Additionally, it provides functionality to generate MD5 checksums and sample directories for Amazon deliveries.

## Prerequisites

- Python >= 3.10

## Installation

```bash
git clone https://github.com/yourusername/amazonmmc.git
cd amazonmmc
pip install .
```
    

## Usage

The AmazonMMC tool accepts several arguments to specify the operations to be performed. Below are the available options:

### Arguments

- `-r, --rootdir` (Required): Specify the root path of the Amazon delivery.
- `-mec, --mec` (Optional): Create MEC XML files.
- `-mmc, --mmc` (Optional): Create MMC XML files.
- `-md5, --md5` (Optional): Create MD5 checksums.
- `-s, --sample` (Optional): Create completed and starting sample directories.
- `-version, --version`: Display the version of the tool.

### Example Commands

1. Create MEC XML files:
    ```bash
    python amazonmmc.py -r /path/to/rootdir --mec
    ```

2. Create MMC XML files:
    ```bash
    python amazonmmc.py -r /path/to/rootdir --mmc
    ```

3. Generate MD5 checksums:
    ```bash
    python amazonmmc.py -r /path/to/rootdir --md5
    ```

4. Create sample directories:
    ```bash
    python amazonmmc.py -r /path/to/rootdir --sample
    ```

5. Display the tool's version:
    ```bash
    python amazonmmc.py --version
    ```

### Combining Options

You can combine multiple options in a single command. For example, to create both MEC and MMC XML files and generate MD5 checksums, run:
```bash
python amazonmmc.py -r /path/to/rootdir --mec --mmc --md5
```

## Contributing

I welcome contributions to improve the tool. Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or issues, please open an issue on the GitHub repository or contact [pixelomen@gmail.com](pixelomen@gmail.com).

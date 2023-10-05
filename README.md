<p align="center">
  <a href="https://github.com/ChimeraPy/WorkerUI"><img src="./docs/images/banner.png" alt="ChimeraPy/WorkerUI"></a>
</p>
<p align="center">
    <em>Worker UI and CLI Components for the ChimeraPy Framework</em>
</p>
<p align="center">
</p>

ChimeraPy is a Scientific, Distributed Computing Framework for Real-time Multimodal Data Retrieval and Processing. This package provides Worker UI and CLI Components for the ChimeraPy Framework

## Installation

Follow these steps to install and set up the ChimeraPy Worker UI and CLI Components:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ChimeraPy/WorkerUI.git
   cd WorkerUI
   ```

2. **Install Node.js**:
   Ensure you have Node.js version 16 or higher installed. If you don't, you can download it from [Node.js official website](https://nodejs.org/).

3. **Build the Web Components**:
   ```bash
   cd web
   npm install
   npm run build
   ```

4. **Install using pip**:
   Ensure you're in the ChimeraPy development environment, then run:
   ```bash
   pip install .
   ```

After following these steps, the Worker UI and CLI components should be set up and ready for use.

## Usage

The Worker UI script provides a Command Line Interface (CLI) (`cp-worker`) with two main subcommands: `connect` and `ui`.

1. **Connect to a ChimeraPy Manager**:
   ```bash
   cp-worker connect --name WORKER_NAME [OPTIONS]
   ```

   Options:
   - `--name`, `-n`: Name of the worker (required).
   - `--id`: Unique identifier for the worker.
   - `--zeroconf`, `-z`: Use zeroconf to find the manager.
   - `--ip`: IP address of the manager.
   - `--port`, `-p`: Port of the manager.
   - `--delete-temp`, `-d`: Delete temporary files after processing.
   - `--wport`, `-wp`: Port to serve the worker on.
   - `--timeout`, `-t`: Timeout for connecting to the manager (default is 20 seconds).

2. **Serve the ChimeraPy Worker UI**:
   ```bash
   cp-worker ui [OPTIONS]
   ```

   Options:
   - `--port`: Port on which to serve the worker UI (default is 8000).

If you're unsure about which options to use, or need more details about a specific subcommand, you can always use the help command:
   ```bash
   cp-worker [subcommand] --help
   ```

## Contributing
Contributions are welcomed! Our [Developer Documentation](https://chimerapy.readthedocs.io/en/latest/developer/index.html) should provide more details in how ChimeraPy works and what is in current development.

## License
[ChimeraPy](https://github.com/ChimeraPy) and [ChimeraPy/WorkerUI](https://github.com/ChimeraPy/WorkerUI) uses the GNU GENERAL PUBLIC LICENSE, as found in [LICENSE](./LICENSE) file.

## Funding Info
This project is supported by the [National Science Foundation](https://www.nsf.gov/) under AI Institute  Grant No. [DRL-2112635](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2112635&HistoricalAwards=false).

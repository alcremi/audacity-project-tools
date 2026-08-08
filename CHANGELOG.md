## [0.1.0] - 2026-07-14


0001  Initial project structure
0002  Add package infrastructure
0003  Add exceptions
0004  Add Audacity pipe
0005  Implement pipe communication
0006  Add Audacity client
0007  Add track model
0008  Add track parser
0009  Add project opening
0010  Add project saving
0011  Add Audacity exit command
0012  Add project model
0013  Extend project model
0014  Load project tracks
0015  Add project converter
0016  Implement ProjectConverter.convert()
0017  Create a main entry point
0018  Add default pipe discovery
0019  Add project scanner
0020  Add a real processing in main (first part)
0021  Extend README.md
0022  Add GitHub Actions workflow
0023  Add argparse command-line interface
0024  Add dry-run mode
0025  Improve command-line output
0026  Handle command-line errors gracefully
0027  Rename exit_project to exit_audacity
0028  Add 'frozen' to class Track
0029  Handle asynchronous project loading
0030  Add Audacity process management
0031  Add Audacity readiness check
0032  Wait for Audacity before connecting
0033  Audacity clean stop
0034  Add AudacitySession class
0035  Add a global api with a unique function 'convert'
0036  Add console entry point
0037  Move directory conversion workflow to public API
0038  Robust Audacity session shutdown
0039  Add logging and resilient batch conversion
0040  Continue batch conversion after project failures
0041  Report failed project conversions
0042  Handle Audacity label tracks in parser
	- Ignore non-wave tracks returned by Audacity
	- Prevent parsing errors on label tracks
	- Add tests for mixed audio/label track responses
0043  Validate projects before conversion
	- Add project validation before starting Audacity
	- Skip projects already converted to aup3
	- Detect missing _data directories
	- Add validation result model and tests
0044  Improve conversion reporting and project validation
0045  Validate converted project output
	- Check that SaveProject2 actually creates the .aup3 file
	- Add timeout while waiting for conversion output
	- Raise ConversionError when output is missing
	- Add success and failure unit tests
0046  Extract conversion report formatting
0047  Add output directory support


### Added

- Initial GitHub repository
- Project skeleton
- Initial documentation
- Coding conventions
- Architecture roadmap

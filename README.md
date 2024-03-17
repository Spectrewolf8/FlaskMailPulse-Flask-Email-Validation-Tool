# FlaskMailPulse

FlaskMailPulse is a robust Python tool for validating email addresses with correct syntax, existence and deliverability.

## Features

- **Syntax Validation**: Validates that a string is of the form `name@example.com`.
- **Deliverability Check**: Optionally checks if the domain name is set up to receive email.
- **Existence Check**: Verifies if the email address actually exists.
- **Friendly Error Messages**: Provides clear and understandable error messages for failed validations.

## Setting Up the Git Project

To set up the Alive Email Validator project on your local machine, follow these steps:

1. **Clone the Repository**: First, clone the repository to your local machine using the following command:

```bash
git clone https://github.com/Spectrewolf8/FlaskMailPulse-Flask-Email-Validation-Tool
```

2. **Navigate to the Project Directory**: Change into the project directory:

```bash
cd FlaskMailPulse-Flask-Email-Validation-Tool
```

3. **Install Dependencies**: Install the required dependencies using pip. It's recommended to use a virtual environment(pipenv) for this:

```bash
pipenv shell
```

or

```bash
pip install -r requirements.txt
```

4. **Run the Application**: You can now run the application using the following command:

```bash
python app.py
```

## Usage

[1]
![image](https://github.com/Spectrewolf8/FlaskMailPulse-Flask-Email-Validation-Tool/assets/69973760/dfa77d71-956f-4484-95bf-ac3547d6a8eb)
[2]
![image](https://github.com/Spectrewolf8/FlaskMailPulse-Flask-Email-Validation-Tool/assets/69973760/dd3e3d0e-5c31-4355-a51e-76d1885a24a7)


## Contributing

Contributions are welcome! To contribute:

1. Fork this repository.
2. Create a new branch on your fork.
3. Make your changes on your branch.
4. Submit a pull request from your branch to this repository.

Your pull request will be reviewed, and a decision will be made whether to merge your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project is based off of [python-email-validator](https://github.com/JoshData/python-email-validator) github repository.
- The libraries used in this project, as listed in the [requirements.txt](requirements.txt) file.

## Contact

For any questions, issues, or suggestions, please open an issue on the GitHub repository.

## Todo
Some features like user identification and background serverless functions need to be added. Email existence verification logic is flawed as of now. If you'd like to contribute to the project, that's be highly appreciated.


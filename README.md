# Alexandria: AI BookMaker

## Quick Start
1. Install required dependencies:

```
pip install -r requirements.txt
```

2. Please add your ChatGPT login details under `src/data/config.json`. For more
details, look at https://github.com/acheong08/ChatGPT/wiki/Setup
```
{
    "email": <ENTER YOUR EMAIL HERE>,
    "password": <PASSWORD>,
    "isMicrosoftLogin": true
}
```

## Create a Book

In order to create a book, run the following commands.

In Windows:
```
./make_book.bat --topic [TOPIC] --fname [book.epub] --authors [YOUR NAME]
```

In Linux:
```
./make_book --topic [TOPIC] --fname [book.epub] --authors [YOUR NAME]
```

## Example Work

You may find example generated books under the `samples` folder.

<b>Example Book 1</b>. Introduction to PyTorch for Computer Vision

Here is a screenshot of the Table of Contents:

![image](https://user-images.githubusercontent.com/63123494/210196886-7c16108e-a3b1-47d0-940c-be5b63f558dc.png)


## Acknowledgements

Made possible by OpenAI's ChatGPT

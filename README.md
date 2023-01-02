# AI BookMaker

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
./make_book.bat --topic [TOPIC]
```

In Linux:
```
./make_book --topic [TOPIC]
```

## Examples

You may find example generated books under `samples`.

![image](https://user-images.githubusercontent.com/63123494/210196769-0874c4f3-495b-486a-a28e-7613131a275a.png)


### Acknowledgements
Made possible by OpenAI's ChatGPT

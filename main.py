import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def main():
    llm = ChatOpenAI(
        model="gpt-4o",
    )
    image_data = encode_image("imgs/user/test.jpg")
    print(image_data[10])
    message = HumanMessage(content=[
        {
            "type": "text", "text": f"""Please describe the image with as much detail as possible. Things to include are:\
- The sky, including cloud formations.
- The landscape, including any mountains, hills, or valleys.
- Any bodies of water, such as rivers, lakes, or oceans.
- Any plantlife noting any particularity in the flora.
- Any wildlife, including animals or insects."""
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
        }
    ])
    result = llm.invoke([message])
    print(result)


if __name__ == "__main__":
    main()

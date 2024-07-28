from infobip_channels.sms.channel import SMSChannel
import os

infobip = SMSChannel.from_auth_params({
    "base_url": os.getenv("INFOBIP_BASE_URL"),
    "api_key": os.getenv("INFOBIP_API_KEY"),
})

# from langchain_community.utilities.infobip import InfobipAPIWrapper
# infobip = InfobipAPIWrapper()


def main():
    # response = infobip.send_sms_message(
    #     {
    #         "messages": [{
    #             "from": "TEST",
    #             "destinations": [{"to": "18645388199"}],
    #             "text": "hi"
    #         }],
    #         "tracking": {
    #             "track": "SMS"
    #         }
    #     }
    # )
    # print(response)
    response = infobip.get_inbound_sms_messages()
    print(response)
    # infobip.run(
    #     to="18645388199",
    #     body="Hello, World!",
    #     sender="Langchain",
    #     channel="sms",
    # )
    return


if __name__ == "__main__":
    main()

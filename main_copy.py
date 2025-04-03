from src.agent.controller.controller import Controller
from src.agent.asr.asr import ASR

def main():
    asr_instance = ASR(model_name="base")
    controller = Controller(asr=asr_instance)

    # Run dialogues indefinetely without closing program
    while True:
        print("-"*20 + ' New Conversation   ' + "-"*20)
        controller.start()
        print("-"*20 + ' Conversation Ended ' + "-"*20)

if __name__ == "__main__":
    main()
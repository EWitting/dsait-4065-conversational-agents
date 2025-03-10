from src.agent.controller.controller import Controller
from src.agent.asr.asr import ASR

def main():
    asr_instance = ASR(model_name="base")

    # Run dialogues indefinetely without closing program
    while True:
        controller = Controller(asr=asr_instance)
        print("-"*20 + ' New Conversation   ' + "-"*20)
        controller.start()
        print("-"*20 + ' Conversation Ended ' + "-"*20)

if __name__ == "__main__":
    main()
from src.agent.controller.controller import Controller

def main():
    controller = Controller()

    # Run dialogues indefinetely without closing program
    while True:
        print("-"*20 + ' New Conversation   ' + "-"*20)
        controller.start()
        print("-"*20 + ' Conversation Ended ' + "-"*20)

if __name__ == "__main__":
    main()
import rti.connextdds as dds
import threading
import time
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["RTI_LICENSE_FILE"] = os.path.join(current_dir, "rti_license.dat")

def read_messages(reader, user_name):
    while True:
        samples = reader.take()
        for s in samples:
            if s.info.valid:
                sender = s.data["sender"]
                message = s.data["message"]
                if sender != user_name:
                    print(f"\n📩 {sender}: {message}")
        time.sleep(0.2)

def run_chat():
    try:
        print("--- 🚀 Starting Chat App ---")

        xml_path = os.path.join(current_dir, "MyChatConfig.xml")
        provider = dds.QosProvider(xml_path)

        participant = provider.create_participant_from_config(
            "ChatParticipantLibrary::ChatParticipant"
        )

        any_writer = participant.find_datawriter("ChatPublisher::ChatWriter")
        any_reader = participant.find_datareader("ChatSubscriber::ChatReader")

        if not any_writer or not any_reader:
            print("❌ خطأ: لم يتم العثور على writer أو reader.")
            return

        writer = dds.DynamicData.DataWriter(any_writer)
        reader = dds.DynamicData.DataReader(any_reader)

        print(f"Domain ID: {participant.domain_id}")
        print("--- ✅ Chat is LIVE! ---")

        user_name = input("Enter your name: ")

        # 🔹 Start thread to continuously read messages
        threading.Thread(target=read_messages, args=(reader, user_name), daemon=True).start()

        while True:
            msg_text = input(f"{user_name}: ")
            if msg_text.lower() == "exit":
                break

            sample = writer.create_data()
            sample["sender"] = user_name
            sample["message"] = msg_text
            writer.write(sample)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_chat()


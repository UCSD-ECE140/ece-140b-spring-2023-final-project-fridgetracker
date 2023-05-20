import speech_recognition as sr
import datetime
import sqlite3

# Initialize the recognizer
r = sr.Recognizer()

# Define the keyword to trigger the action
keyword = "hello kitchen"

# Connect to the database
conn = sqlite3.connect('items.db')
c = conn.cursor()

# Create a table to store items
c.execute('''CREATE TABLE IF NOT EXISTS items
             (name TEXT, expiration_date DATE)''')
conn.commit()

# Start listening to the microphone
with sr.Microphone() as source:
    print("Listening...")
    while True:
        audio = r.listen(source)

        try:
            # Recognize speech using Google Speech Recognition
            text = r.recognize_google(audio)
            print("Heard:", text)

            # Check if the keyword is present in the recognized text
            if keyword in text:
                # Extract the action from the recognized text
                action = text.split(keyword)[1].strip().lower()
                print("Action:", action)

                # Perform actions based on the recognized command
                if action.startswith("add"):
                    item = action.split("add")[1].strip()
                    # Check if the item is for the fridge list
                    if "to fridge list" in action:
                        print("Adding", item, "to the fridge list")
                        # Get the expiration date from the user
                        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
                        # Insert the item and expiration date into the database
                        c.execute("INSERT INTO items (name, expiration_date) VALUES (?, ?)",
                                  (item, expiration_date))
                        conn.commit()
                        print("Item added to the fridge list")

                    # Check if the item is for the pantry list
                    elif "to pantry list" in action:
                        print("Adding", item, "to the pantry list")
                        # Get the expiration date from the user
                        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
                        # Insert the item and expiration date into the database
                        c.execute("INSERT INTO items (name, expiration_date) VALUES (?, ?)",
                                  (item, expiration_date))
                        conn.commit()
                        print("Item added to the pantry list")

                    # Check if the item is for the counter list
                    elif "to counter list" in action:
                        print("Adding", item, "to the counter list")
                        # Get the expiration date from the user
                        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
                        # Insert the item and expiration date into the database
                        c.execute("INSERT INTO items (name, expiration_date) VALUES (?, ?)",
                                  (item, expiration_date))
                        conn.commit()
                        print("Item added to the counter list")

                    # Check if the item is for the shopping list
                    elif "to shopping list" in action:
                        print("Adding", item, "to the shopping list")
                        # Get the expiration date from the user
                        expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
                        # Insert the item and expiration date into the database
                        c.execute("INSERT INTO items (name, expiration_date) VALUES (?, ?)",
                                  (item, expiration_date))
                        conn.commit()
                        print("Item added to the shopping list")

                    else:
                        print("Invalid target list")

                elif action.startswith("delete"):
                    item = action.split("delete")[1].strip()
                    # Check if the item is for the fridge list
                    if "from fridge list" in action:
                        print("Deleting", item, "from the fridge list")
                        # Delete the item from the database
                        c.execute("DELETE FROM items WHERE name=?", (item,))
                        conn.commit()
                        print("Item deleted from the fridge list")

                    # Check if the item is for the pantry list
                    elif "from pantry list" in action:
                        print("Deleting", item, "from the pantry list")
                        # Delete the item from the database
                        c.execute("DELETE FROM items WHERE name=?", (item,))
                        conn.commit()
                        print("Item deleted from the pantry list")

                    # Check if the item is for the counter list
                    elif "from counter list" in action:
                        print("Deleting", item, "from the counter list")
                        # Delete the item from the database
                        c.execute("DELETE FROM items WHERE name=?", (item,))
                        conn.commit()
                        print("Item deleted from the counter list")

                    # Check if the item is for the shopping list
                    elif "from shopping list" in action:
                        print("Deleting", item, "from the shopping list")
                        # Delete the item from the database
                        c.execute("DELETE FROM items WHERE name=?", (item,))
                        conn.commit()
                        print("Item deleted from the shopping list")

                    else:
                        print("Invalid target list")
                else:
                    print("Invalid action")

        except sr.UnknownValueError:
            print("Could not understand audio")

        except sr.RequestError as e:
            print("Error: {0}".format(e))

# Close the database connection
conn.close()

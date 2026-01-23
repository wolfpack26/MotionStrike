print("Choose Mode:")
print("1 - Stick Mode")
print("2 - Hand Mode")

choice = input("Enter 1 or 2: ")

if choice == "1":
    import sticks
elif choice == "2":
    import hand_tracked
else:
    print("Invalid choice")

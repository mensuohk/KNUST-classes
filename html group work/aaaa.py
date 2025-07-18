x = int(input("Enter a scrore: "))
if x < 40:
    print("F")
elif x >= 40 and x <= 49:
    print("E")
elif x >= 50 and x <= 59:
    print("D")
elif x >= 60 and x <= 69:       
    print("C")
elif x >= 70 and x <= 79:
    print("B")     
else:
    print("A")
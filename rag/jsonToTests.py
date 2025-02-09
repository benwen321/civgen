import json
finalString = ""
with open("gemini-2.0-flash_test_questions.json", "r") as f:
    data = json.load(f)
    for question in data:
        finalString += "##QUERY\n"
        for line in question["questions"]:
            finalString += line + "\n"
        finalString += "##EXPECTEDRESULTS\n"
        finalString += question["page"] + "\n"
    with open("gemini-2.0-flash_test_questions.json.txt", "w") as f:
        f.write(finalString)



    
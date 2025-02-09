import argparse
from runRagQuery import *

def loadQueries(queryFile):
    with open(queryFile) as f:
        lines = f.readlines()
    # split the lines into sections
    # the sections are separated by a line that starts with "##"
    # the sections, which are repeated, are currently QUERY, EXPECTEDRESULTS
    queriesWithResults = []
    currentSection = "START"
    curQuery = [[],[]]
    i = 0
    for line in lines:
        
        if line.startswith("##"):
            print(line)
            if currentSection != "START" and (line[2:].strip() == "QUERY" or line[2:].strip() == "END"):
                if len(curQuery[0]) == 0:
                    raise Exception(f"At least one query has no query text. line number {i} in file {queryFile}.")
                if len(curQuery[1]) == 0:
                    raise Exception("At least one query has no expected results.")
                queriesWithResults.append(curQuery) 
                curQuery = [[],[]]
            currentSection = line[2:].strip()
        else:
            if currentSection == "QUERY":
                curQuery[0].append(line.strip())
            elif currentSection == "EXPECTEDRESULTS":
                curQuery[1].append(line.strip())
        i += 1

    # if any are empty, raise an error
    if len(queriesWithResults) == 0:
        raise Exception("No queries found in query file.")
    return queriesWithResults


def loadTestSuite(testFile):
    with open(testFile) as f:
        lines = f.readlines()
    # split the lines into sections
    # the sections are separated by a line that starts with "##"
    # the sections are currently QUERYFILES, TESTMETHODS, EXPECTEDRESULTS
    queryFiles = []
    testMethods = []
    expectedResults = []
    currentSection = ""
    for line in lines:
        if line.startswith("##"):
            currentSection = line[2:].strip()
        else:
            if currentSection == "QUERYFILES":
                queryFiles.append(line.strip())
            elif currentSection == "TESTMETHODS":
                testMethods.append(line.strip())
            elif currentSection == "EXPECTEDRESULTS":
                expectedResults.append(line.strip())
    # if any are empty, raise an error
    if len(queryFiles) == 0:
        raise Exception("No query files found in test suite.")
    if len(testMethods) == 0:
        raise Exception("No test methods found in test suite.")
    if len(expectedResults) == 0:
        raise Exception("No expected results found in test suite.")
    # if testMethods and expectedResults are not the same length, raise an error
    if len(testMethods) != len(expectedResults):
        raise Exception("Number of test methods and expected results do not match.")
    
    # now open the query files and load the queries
    queries = []
    for queryFile in queryFiles:
        queries = queries + loadQueries(queryFile)
    # now return the test suite
    return queries, testMethods, expectedResults

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RAG test suite.')
    parser.add_argument('--testFile', help='Test name to run.',required=True)
    parser.add_argument('--dataPath', help='Data path to use.',required=False,default='dmv_site_data_base')
    parser.add_argument('--timesToRun', help='Number of times to run the tests.',required=False,default=1)
    parser.add_argument('--k', help='k val.',default=5,required=False)

    args = parser.parse_args()
    testFile = args.testFile
    timesToRun = int(args.timesToRun)
    dataPath = args.dataPath
    k = int(args.k)
    # Load the test suite  
    queries, testMethods, expectedResults = loadTestSuite(testFile)
    finalResults = []
    for i in range(timesToRun):
        for query in queries:
            curResult = []
            for text in query[0]:
                for j in range(len(testMethods)):
                    testMethod = testMethods[j]
                    expectedResult = expectedResults[j]
                    # print(f"Running test method {testMethod} with expected result {expectedResult}")
                    # run the test method
                    redisQuery, queryVector = eval(testMethod+"(text,k)")
                    # check the result
                    # run the vector
                    result = runRagQuery(getRedisClient(), dataPath,redisQuery,queryVector)
                    i = 0
                    valResults = 0
                    for eResult in query[1]:
                        j = 0
                        while j < len(result.docs):
                            if eResult == result.docs[j].page:
                                valResults += j -i 
                            j += 1
                        if eResult not in [x.page for x in result.docs]:
                            valResults += 2
                            print(f"Expected result {eResult} not found in results.")
                        i += 1
                    print(f"Test method {testMethod} with expected result {eResult} has value {valResults}")
                    curResult.append(valResults)
            finalResults.append(curResult)
    print(finalResults)
    print(sum([sum(x) for x in finalResults]))
    if sum([sum(x) for x in finalResults]) < int(expectedResults[0]):
        print("All tests passed.")

    # go through the queries and print the fails 
    for i in range(len(finalResults)):
        for j in range(len(finalResults[i])):
            if finalResults[i][j] > 0:
                print(f"{queries[i][0][j]}: {finalResults[i][j]}, expected {queries[i][1]}")
            


                            



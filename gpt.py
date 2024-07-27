import json

def search_for_cars(client, prompt):
    raw_result = client.chat.completions.create(
      model="gpt-4o",
      messages=[{
          "role":
          'system',
          "content":
          """You are a search engine that looks for cars based on the requirements provided on the Malaysian car listing marketplace like mudah.my, Carlist, Carro and more.
          You must follow ALL the requirements provided and search for car options on MALAYSIAN car website only.
          If possible, include the engine/tier choices of the car, for example: Do not just specify "BMW X3" or "Mercedes-Benz GLC", specify in more detail like "BMW X3 30i" and "Mercedes-Benz GLC300". 
          There is an 'extras' section as a part of the input, which you can ignore if it has no actual meaning. Otherwise, you must include it as a part of the search. 
          Your output is a python array of cars. Each car is an array with the brand, model, year, average market value, and link to the marketplace(s) it was found on.
          Example of output is [["BMW", "323i",2011,30000, ["mudah.my", "carlist.my"]], ["Mercedes-Benz", "C230", 2010,30000, ["carlist.my"]]]
          If no cars are found for the requirements, output an empty array []. Note that the average market value MUST be in Malaysian Ringgit only.
          The maximum number of cars in the output is 4. 
          """
      }, {
          "role": "user",
          "content": f'{prompt}'
      }],
      max_tokens=500,
      temperature=0.5)

    result = raw_result.choices[0].message.content

    print(result)
    print(type(result))
    print("\n")
    result = result[9:-3]
    print(result)

    try:
      cars = json.loads(result)
    except json.JSONDecodeError:
      cars = []

    print(cars)
    return cars

def search_for_prices(client, prompt):
    raw_result = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
                'system',
            "content":
                """You are a search engine that looks for the average market value based on the car specifications provided on the Malaysian car listing marketplace like mudah.my, Carlist, Carro and more.
                You must follow ALL the specifications provided and search for car options in Malaysia only.
                Your output is an integer - ie: the average market value of that car. Do not include the currency, only include the value. 
                If the average market value of that car is not available (or the car does not exist at all) output -1. 
                Note that the average market value MUST be in Malaysian Ringgit only.
                """
        }, {
            "role": "user",
            "content": f'{prompt}'
        }],
        max_tokens=50,
        temperature=0.5)

    print(raw_result)
    result = raw_result.choices[0].message.content
    return result
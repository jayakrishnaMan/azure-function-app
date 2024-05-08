import azure.functions as func
import logging
import json
import requests

# Sentences are encoded by calling model.encode()
model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = "s" #"get your token in http://hf.co/settings/tokens"


api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}



app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_custom_embedding")
def get_custom_embedding(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        values = req_body['values']
        output = []
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        for i in range(0,len(values)):
            value=values[i]
            input_text_question=value['data']['question']
            input_text_answer=value['data']['question']
                #             {
                #     "values": [
                #         {
                #             "recordId": "1234",
                #             "data": {
                #                 "text": "This is a test document."
                #             }
                #         }
                #     ]
                # }

            try:

                response = requests.post(api_url, headers=headers, json={"inputs": input_text_question, "options":{"wait_for_model":True}})
                embedding_output=response.json()
                # embedding = model.encode(input_text) #for cys
                questionvector=embedding_output
                response = requests.post(api_url, headers=headers, json={"inputs": input_text_answer, "options":{"wait_for_model":True}})
                embedding_output=response.json()
                # embedding = model.encode(input_text) #for cys
                answervector=embedding_output
                output.append({
                    'recordID':values[i]['recordId'],
                    "data":{ "answerVector":answervector,
                            
                                "questionVector":questionvector
                    }
                })
            #                 {
            #     "values": [
            #         {
            #             "recordId": "1234",
            #             "data": {
            #                 "vector": [
            #                     -0.03833850100636482,
            #                     0.1234646588563919,
            #                     -0.028642958030104637,
            #                     . . . 
            #                 ]
            #             },
            #             "errors": null,
            #             "warnings": null
            #         }
            #     ]
            # }
            except Exception as e:
                print("Eddddd",e)
                values[i]['data']['errors']="There is a error during processing"
                output.append({
                                    'recordID':values[i]['recordId'],
                                      "errors": [{"message":"error is"+e}],
                                })
            # del values[i]['data']['question']
            # del values[i]['data']['question']
            z={"values":output}
            print("Eddddd",z)
            logging.info(f'RUD: {z}')
            return func.HttpResponse(
                json.dumps({"values":output}),
                mimetype="application/json",
                status_code=200
            )
    except Exception as e:
        print("error is ",e)
        return func.HttpResponse(
                json.dumps({"values":output}),
                mimetype="application/json",
                status_code=401
            )
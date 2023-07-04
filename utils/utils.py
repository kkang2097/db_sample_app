import requests

def generic_api_requests(method, url, payload={}, params={}):
    print("CURRENT REQUEST : ", method, url, payload)

    try:
        response = requests.request(
            method,
            url,
            json=payload,
            params=params,
        )

        json_response = response.json()

        print( "RESPONSE SUCCESS")

        return 1, json_response

    except Exception as e:
        print("RESPONSE ERROR :", e)
        return 0, e
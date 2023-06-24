import axios, { AxiosError } from "axios";
import apiUrl from "../../config";

const availableEndpoints = ["market", "symbols", "symbols-list"]

function fetchBackend(endpoint, method, data = {}, params = {}) {

    return axios({
        method: method,
        url: apiUrl + endpoint,
        data: data,
        params: params
    }).then((res) => {

        switch (method) {
            case 'get':
                switch (res.status) {
                    case 200:
                        return res.data
                    case 204:
                        // Data does not exists
                        return fetchBackend(endpoint, 'post', {}, params)
                }

            case 'post':
                // Data either already exists or was created, get it anyway
                if (Object.keys(data).includes("symbol")) {
                    // Symbol was created, must update endpoint to get it
                    return fetchBackend(endpoint + "/" + data.symbol, 'get', data, params)
                } else {
                    return fetchBackend(endpoint, 'get', data, params)
                }


            case 'put':
                switch (res.status) {
                    case 200:
                        // Data successfully updated, now get it
                        return fetchBackend(endpoint, 'get', data, params)
                    case 204:
                        // Data does not exist
                        // TODO : not convenient, should not change endpoint -> change the backend endpoints ?
                        if (endpoint.substring(0, 8) == 'symbols/') {
                            // Trying to update a specific data symbol
                            // Post method is not at same endpoint (dumb idea...)

                            return fetchBackend("symbols", 'post', { symbol: endpoint.substring(8), timeDelta: params.timeDelta }, params)
                        } else { return fetchBackend(endpoint, 'post') }

                }
        }


    }).catch((error) => {

        // Not Modified error
        if (error.response.status == 304) {
            return fetchBackend(endpoint, 'get', data, params)
        } else if (error.response.status == 500) {
            console.log("Erreur 500")
        } else {
            throw AxiosError
        }

    })

}

export { fetchBackend }
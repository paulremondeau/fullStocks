import axios from "axios";
import apiUrl from "../../config";

import { useNotification } from "@kyvg/vue3-notification";
const { notify } = useNotification()

const availableEndpoints = ["market", "symbols", "symbols-list"]

function fetchBackend(endpoint, method, controller, data = {}, params = {}) {

    if (controller == undefined) {
        controller = new AbortController();
    }


    return axios({
        method: method,
        url: apiUrl + endpoint,
        data: data,
        params: params,
        signal: controller.signal
    }).then((res) => {

        switch (method) {
            case 'get':
                switch (res.status) {
                    case 200:
                        return { "data": res.data, "status": "ok" }
                    case 204:
                        // Data does not exists
                        return fetchBackend(endpoint, 'post', controller, {}, params)
                }

            case 'post':
                // Data either already exists or was created, get it anyway
                if (Object.keys(data).includes("symbol")) {
                    // Symbol was created, must update endpoint to get it
                    return fetchBackend(endpoint + "/" + data.symbol, controller, 'get', data, params)
                } else {
                    return fetchBackend(endpoint, 'get', controller, data, params)
                }


            case 'put':
                switch (res.status) {
                    case 200:
                        // Data successfully updated, now get it
                        return fetchBackend(endpoint, 'get', controller, data, params)
                    case 204:
                        // Data does not exist
                        // TODO : not convenient, should not change endpoint -> change the backend endpoints ?
                        if (endpoint.substring(0, 8) == 'symbols/') {
                            // Trying to update a specific data symbol
                            // Post method is not at same endpoint (dumb idea...)

                            return fetchBackend("symbols", 'post', controller, { symbol: endpoint.substring(8), timeDelta: params.timeDelta }, params)
                        } else { return fetchBackend(endpoint, 'post') }

                }
        }


    }).catch((error) => {
        if (error.code == "ERR_CANCELED") {
            return { "status": "error" }
        } else {
            // Not Modified error
            if (error.response.status == 304) {
                return fetchBackend(endpoint, 'get', controller, data, params)
            } else if (error.response.status == 500) {
                notify({
                    title: "⚠️ " + error.response.data.message,
                    group: 'Error',
                    type: 'error',
                });
                return { "status": "error" }
            } else {
                return { "status": "error" }
            }

        }
    })

}


export { fetchBackend }




import { describe, it, expect } from 'vitest'

import { fetchBackend } from '../fetchbackend'

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import apiUrl from "../../../config";


describe('fetchBackend', () => {



    it('should work', () => {

        var mock = new MockAdapter(axios);
        const data = { "foo": 0 };

        mock.onGet(apiUrl + "market").reply(200, data)


        fetchBackend("market", "get").then(response => {

            expect(response).toStrictEqual({ data: { foo: 0 }, status: 'ok' })
        })
    })

    it('symbol pipeline works', () => {

        var mock = new MockAdapter(axios);
        const data = { "foo": 0 };
        const symbol = "FOO"

        mock.onPut(apiUrl + "symbols/" + symbol).reply(204) // Does not exists
        mock.onPost(apiUrl + "symbols").reply(201) // Data created
        mock.onGet(apiUrl + "symbols/" + symbol).reply(200, data)


        fetchBackend("symbols/" + symbol, "put", undefined, { symbol: symbol }, { timeDelta: "4h", performance: false }).then(response => {

            expect(response).toStrictEqual({ data: { foo: 0 }, status: 'ok' })
        })
    })


})


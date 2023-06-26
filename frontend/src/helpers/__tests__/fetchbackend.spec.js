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

            expect(response).toStrictEqual({ data: { foo: 1 }, status: 'ok' })
        })
    })


})


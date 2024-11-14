export const batchApiCalls = async (requests) => {
  const payload = {
    batch: requests,
  };

  const response = await fetch(`${process.env.REACT_APP_API_ENDPOINT}/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  return data;
};

export const createRequest = (endpoint, method = 'GET', body = null) => {
  return {
    endpoint,
    method,
    body, 
  };
};

import React, { createContext, useContext, useState } from 'react';
import { batchApiCalls, createRequest } from './api'; 

const DataContext = createContext();

export const DataProvider = ({ children }) => {
  const [data, setData] = useState(null);

  const fetchData = async (endpoints = [process.env.REACT_APP_API_ENDPOINT]) => {
    if (data) return data; 

    const requests = endpoints.map((endpoint) => createRequest(endpoint));
    const newData = await batchApiCalls(requests);

    setData(newData);
    return newData;
  };

  return (
    <DataContext.Provider value={{ data, fetchData }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => useContext(DataContext);
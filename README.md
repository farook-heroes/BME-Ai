# Health AI Logic
Backend logic for Health AI

# Endpoints

## /models

This endpoint will provide information about the models available

Format in which the enpoint returns

```
{
    models: [
        {
            name: string
            description: string
            endpoint: string
            args: [
                {
                    name: string
                    description: string
                }
            ]
        }
    ]
}
```


## /predict/\<endpoint\>

This endpoint will make the predictions

on success it returns
```
{
    result: [float]
}
```
on error it returns
```
{
    error: string
    description: string
}
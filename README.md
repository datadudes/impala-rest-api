#  Impala REST API

**This is WIP!**

Thin server to provide REST API for Cloudera Impala, written in Python.

## Example usage

Assume the server is running on `impala-api.example.com`.

Retrieve top 10 customers in CSV format, including the table header in CSV:

```
$ curl -X POST impala-api.example.com/impala?header=true \
  --data 'select * from customers limit 5' \
  --header 'Accept: text/csv'

name,city,age  
Peter,Dublin,55
Daan,Harlem,34
Jan,Amsterdam,15
Adam,Zurich,22
Marcel,Amsterdam,89
```

## Installation

todo

## Configuration

todo

### Contributions:

Please create an issue if you spot any problem or bug.
We'll try to get back to you as soon as possible.

### Authors:

Created with passion by [Marcel](https://github.com/mkrcah)
and [Daan](https://github.com/DandyDev).

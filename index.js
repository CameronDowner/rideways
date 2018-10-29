const express = require('express')
const app = express()

const { PythonShell } = require('python-shell')

const coordinateRegex = /^\-?\d\.\d{6},\-?\d\.\d{6}$/
function isInvalidCoordinate(input) {
    return !input.match(coordinateRegex)
}

function getMissingParameters(pickup, dropoff, passengers) {
    const missingParameters = []

    if (!pickup) {
        missingParameters.push('pickup')
    }

    if (!dropoff) {
        missingParameters.push('dropoff')
    }

    if (!passengers) {
        missingParameters.push('passengers')
    }

    return missingParameters
}

function getValidationError(pickup, dropoff, passengers) {
    const missingParameters = getMissingParameters(pickup, dropoff, passengers)
    if (missingParameters.length > 0) {
        return `The query parameters '${missingParameters.join(',')}' are required.`
    }

    if (isNaN(passengers)) {
        return 'passengers parameter must be a number'
    }

    if (isInvalidCoordinate(pickup)) {
        return 'pickup parameter has an invalid format'
    }

    if (isInvalidCoordinate(dropoff)) {
        return 'dropoff parameter has an invalid format'
    }

    return null
}

function parseRow(row) {
    const option = row.split('-').map(item => item.trim())

    return {
        car_type: option[0],
        supplier: option[1],
        price: parseInt(option[2])
    }
}

function parseResults(results) {
    return results.map(parseRow)
}

app.get('/', (req, res) => {
    const { pickup, dropoff, passengers } = req.query

    const error = getValidationError(pickup, dropoff, passengers)

    if (error) {
        return res.json({ error })
    }

    const options = {
        args: [pickup, dropoff, passengers]
    }

    PythonShell.run('rideways.py', options, function (err, results) {
        if(err) {
            return res.json({ err })
        }

        const options = parseResults(results)
        
        return res.json({ options })
    })
})

const port = 3000
app.listen(port, () => console.log(`Example app listening on port ${port}!`))
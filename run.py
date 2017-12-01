#!/usr/bin/env python
# -*- coding: utf-8 -*-


from app import app

# app = create_app(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009, debug=True)

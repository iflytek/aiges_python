proto:
	python -m grpc_tools.protoc -I .  --python_out=. --grpc_python_out=. ././aiges/aiges_inner/aiges_inner.proto && echo "success generated"
	poetry build
	pip install ./dist/aiges-0.5.1.tar.gz

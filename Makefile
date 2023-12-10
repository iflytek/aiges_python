proto:
	python -m grpc_tools.protoc -I .  --python_out=. --grpc_python_out=. ././aiges/aiges_inner/aiges_inner.proto && echo "success generated"
	python -m grpc_tools.protoc -I .  --pyi_out=. --python_out=. --grpc_python_out=. ././aiges/protocol/xsf.proto && echo "success generated"

	poetry build
	ls -lt dist | grep "tar.gz" | head -n 1 |awk '{print "./dist/"$$9}' |xargs pip install

publish:
	poetry publish
publish-custom:
	poetry publish -r my-custom-repo

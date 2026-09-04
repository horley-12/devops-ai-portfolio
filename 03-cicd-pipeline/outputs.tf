output "lambda_function_name" {
  value = aws_lambda_function.api.function_name
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.players.name
}

output "lambda_arn" {
  value = aws_lambda_function.api.arn
}

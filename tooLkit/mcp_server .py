"""
MCP Server for Hybrid Math Toolkit
يجعل الأداة قابلة للاستدعاء من Claude, ChatGPT
"""
import json, sys
from hybrid_math_toolkit import verified_solve

MCP_TOOLS = [
    {
        "name": "verified_solve",
        "description": "حل نظام معادلات خطية مع تحقق رياضي كامل. لا يهلوس - يتحقق أن A·x-b=0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "نص المسألة، كل معادلة في سطر. مثال: 'x + y = 3\\nx - y = 1'"
                },
                "strict": {
                    "type": "boolean",
                    "description": "إذا True، أي تناقض يرجع INCONSISTENT",
                    "default": False
                }
            },
            "required": ["problem"]
        }
    }
]

def handle_tool_call(tool_name, arguments):
    problem = arguments.get("problem", "")
    strict = arguments.get("strict", False)
    if tool_name == "verified_solve":
        return verified_solve(problem, strict=strict)
    return {"error": f"أداة غير معروفة: {tool_name}"}

def run_mcp_server():
    print("MCP Server: Hybrid Math Toolkit - جاهز", file=sys.stderr)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            if method == "tools/list":
                response = {"jsonrpc": "2.0","id": request.get("id"),"result": {"tools": MCP_TOOLS}}
                print(json.dumps(response))
            elif method == "tools/call":
                params = request.get("params", {})
                result = handle_tool_call(params.get("name"), params.get("arguments", {}))
                response = {
                    "jsonrpc": "2.0","id": request.get("id"),
                    "result": {"content": [{"type": "text","text": json.dumps(result, ensure_ascii=False, indent=2)}]}
                }
                print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"jsonrpc":"2.0","id":0,"error":{"code":-1,"message":str(e)}}))
            sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        print(verified_solve("x + y = 3\nx - y = 1"))
    else:
        run_mcp_server()

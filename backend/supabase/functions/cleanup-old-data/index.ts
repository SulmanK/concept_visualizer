import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const handler = async (_req: Request) => {
  try {
    // Run the Python script
    const command = new Deno.Command("python3", {
      args: ["handler.py"],
      stdout: "piped",
      stderr: "piped",
    });
    
    const process = command.spawn();
    const output = await process.output();
    const outStr = new TextDecoder().decode(output.stdout);
    const errStr = new TextDecoder().decode(output.stderr);
    
    if (errStr) {
      console.error("Error running cleanup script:", errStr);
      return new Response(JSON.stringify({ error: errStr }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
    
    return new Response(JSON.stringify({ message: "Cleanup completed", details: outStr }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("Failed to run cleanup script:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

serve(handler); 
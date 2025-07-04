import {
  createFileRoute,
  useRouter,
  useSearch,
  redirect,
} from "@tanstack/react-router";
import { useState } from "react";
import { useForm, type SubmitHandler } from "react-hook-form";
import { isAuthenticated } from "../api/auth";
import { API_BASE } from "../config/api";

// ——— Types ———
interface LoginFormData {
  trader_id: number;
}

// ——— Route Definition ———
export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (await isAuthenticated()) {
      throw redirect({
        to: "/",
      });
    }
  },
});

// ——— Component ———
function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const router = useRouter();
  const search = useSearch({ from: "/login" });
  const [error, setError] = useState(null);

  const handleLoginSubmit: SubmitHandler<LoginFormData> = async (
    data: LoginFormData
  ) => {
    const trader_id = data.trader_id;

    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trader_id }),
    });

    if (res.ok) {
      router.history.push(search.redirect ?? "/");
    } else {
      const errorData = await res.json(); // 👈 this parses the error body
      const errorMessage = errorData.detail || "Unknown error";
      console.error(errorMessage);
      setError(errorData.detail);
    }
  };

  return (
    <div className="p-2">
      <h3 className="text-lg font-semibold mb-2">
        Please log in before continuing
      </h3>

      <form
        onSubmit={handleSubmit(handleLoginSubmit)}
        className="flex items-end"
      >
        <div>
          <label htmlFor="trader_id" className="block mb-1">
            Trader ID
          </label>
          <input
            id="trader_id"
            type="text"
            placeholder="Enter your trader ID"
            {...register("trader_id", {
              required: "Trader ID is required",
              valueAsNumber: true,
              validate: (v) => !isNaN(v) || "Must be a number",
            })}
            aria-invalid={errors.trader_id ? "true" : "false"}
            className={`bg-slate-200 rounded-2xl p-2 text-black ${errors.trader_id ? "border border-red-500" : ""}`}
          />
        </div>
        <div>
          <input
            type="submit"
            value="Log in"
            className="bg-blue-400 rounded-2xl p-2 text-white mx-8  h-10"
          />
        </div>
      </form>
      {errors.trader_id && (
        <p className="text-red-600 mt-1 text-sm">{errors.trader_id.message}</p>
      )}
      {error && <p className="text-red-600 mt-1 text-sm">{error}</p>}
    </div>
  );
}

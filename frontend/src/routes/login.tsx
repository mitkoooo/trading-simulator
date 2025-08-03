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
  trader_id: string;
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
    data: LoginFormData,
  ) => {
    const trader_id = data.trader_id;

    const res = await fetch(`${API_BASE}/users/login`, {
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
      <h3 className="mb-2 text-lg font-semibold">
        Please log in before continuing
      </h3>

      <form
        onSubmit={handleSubmit(handleLoginSubmit)}
        className="flex items-end"
      >
        <div>
          <label htmlFor="trader_id" className="mb-1 block">
            Trader ID
          </label>
          <input
            id="trader_id"
            type="text"
            placeholder="Enter your trader ID"
            {...register("trader_id", {
              required: "Trader ID is required",
            })}
            aria-invalid={errors.trader_id ? "true" : "false"}
            className={`rounded-2xl bg-slate-200 p-2 text-black ${errors.trader_id ? "border border-red-500" : ""}`}
          />
        </div>
        <div>
          <input
            type="submit"
            value="Log in"
            className="mx-8 h-10 rounded-2xl bg-blue-400 p-2 text-white"
          />
        </div>
      </form>
      {errors.trader_id && (
        <p className="mt-1 text-sm text-red-600">{errors.trader_id.message}</p>
      )}
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}

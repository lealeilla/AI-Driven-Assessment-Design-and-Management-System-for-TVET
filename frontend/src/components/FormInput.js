function FormInput({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder,
  error,
  inputClassName = ""
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-700">{label}</span>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-2xl border bg-slate-50 px-4 py-3.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white ${
          error ? "border-red-300" : "border-slate-200"
        } ${inputClassName}`}
      />
      {error ? <span className="mt-2 block text-xs text-red-500">{error}</span> : null}
    </label>
  );
}

export default FormInput;

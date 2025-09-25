import express, { Request, Response } from "express";
import cors from "cors";

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

app.get("/api/key", (req: Request, res: Response) => {
  res.json({ key: "ts-powered-fvtt-key" });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});

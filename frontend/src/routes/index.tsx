import { Box, Button, Heading, Image, Text, Textarea } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import useCustomToast from "../hooks/useCustomToast"

export default function HomePage() {
  const [prompt, setPrompt] = useState<string>("")
  const [result, setResult] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const { showErrorToast } = useCustomToast()

  useEffect(() => {
    let objectUrl: string | null = null;

    if (result) {
      objectUrl = result;
    }

    // Clean up the object URL when the component unmounts
    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [result]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!prompt.trim()) {
      showErrorToast("プロンプトを入力してください。")
      return
    }

    setIsLoading(true)
    setResult("")

    try {
      const formData = new FormData()
      formData.append("generator_name", "text_gemini_pro_v1") // Or make this selectable
      formData.append("prompt", prompt)

      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiUrl}/api/v1/circuits/generate-and-render`,
        {
          method: "POST",
          body: formData,
        },
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => null); // Try to parse error response
        const errorMessage = errorData?.detail || `HTTP error! status: ${response.status}`;
        throw new Error(errorMessage);
      }

      const svg = await response.text()
      const blob = new Blob([svg], { type: "image/svg+xml" })
      const url = URL.createObjectURL(blob)
      setResult(url)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      console.error("API call failed:", errorMessage);
      showErrorToast(errorMessage);
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      minH="100vh"
      bg="gray.100"
      p={8}
    >
      <Heading as="h1" size="xl" color="gray.800" mb={6}>
        Circuit Craft AI
      </Heading>
      <Text fontSize="lg" color="gray.600" mb={8}>
        作りたい回路を文章で説明してください
      </Text>

      <Box
        as="form"
        onSubmit={handleSubmit}
        w="full"
        maxW="2xl"
        bg="white"
        p={6}
        borderRadius="lg"
        boxShadow="md"
      >
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 1.5Vの乾電池と330Ωの抵抗、赤色LEDを直列に接続してください。"
          disabled={isLoading}
          size="lg"
          height="160px"
        />
        <Button
          type="submit"
          w="full"
          mt={4}
          colorScheme="blue"
          loading={isLoading}
          loadingText="生成中..."
        >
          回路図を生成
        </Button>
      </Box>

      {result && (
        <Box
          w="full"
          maxW="2xl"
          mt={8}
          bg="white"
          p={6}
          borderRadius="lg"
          boxShadow="md"
        >
          <Heading as="h2" size="lg" color="gray.800" mb={4}>
            生成結果 (SVG)
          </Heading>
          <Box border="1px" borderColor="gray.200" borderRadius="md" p={4}>
            <Image src={result} />
          </Box>
        </Box>
      )}
    </Box>
  )
}
